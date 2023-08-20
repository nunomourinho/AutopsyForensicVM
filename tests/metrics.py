import cpuinfo

try:  
    from time import perf_counter as time
except ImportError:  
    if sys.platform[:3] == 'win':
        from time import clock as time
    else:
        from time import time
import os, sys
from random import shuffle
import argparse
import json
import speedtest
import paramiko
import os
import platform
import subprocess
import win32api
import psutil
import subprocess
from statistics import mean

def get_physical_drive_from_letter(letter):
    cmd = f'(Get-Partition -DriveLetter {letter}).DiskNumber'
    result = subprocess.check_output(["powershell", cmd], text=True).strip()
    return result

def get_linux_disk_type(file_path):
    # Getting the root device of the file
    df_command = ['df', '-P', file_path]
    root_device = subprocess.check_output(df_command).decode().split("\n")[1].split()[0]

    # Using lsblk to get the type of the device
    lsblk_command = ['lsblk', '-ndo', 'type', root_device]
    device_type = subprocess.check_output(lsblk_command).decode().strip()

    # If the device type is 'disk', we try to further determine its type using udevadm
    if device_type == 'disk':
        udevadm_command = ['udevadm', 'info', '--query=all', '--name=' + root_device]
        output = subprocess.check_output(udevadm_command).decode()
        if "ID_BUS=ata" in output:
            return "SATA"
        if "ID_BUS=scsi" in output:
            return "SCSI"
        if "ID_SERIAL_SHORT=Nvme" in output:
            return "NVMe"
    return device_type

def get_windows_disk_type(file_path):
    import win32file
    import win32com.client
    import os

    # Extract the drive letter
    drive_letter = file_path[0]
    drive_number = get_physical_drive_from_letter(drive_letter)    

    wmi = win32com.client.GetObject("winmgmts:")
    attributes_tuples = []

    for disk in wmi.InstancesOf("Win32_DiskDrive"):
        if int(disk.Index) == int(drive_number):
            attributes_tuples.append(("disk_model", disk.Model))
            attributes_tuples.append(("disk_caption", disk.Caption))
            attributes_tuples.append(("disk_index", disk.Index))
            attributes_tuples.append(("disk_name", disk.Name))
            attributes_tuples.append(("disk_media_type", disk.MediaType))
            attributes_tuples.append(("disk_status", disk.Status))
            try:
                attributes_tuples.append(("disk_size_GB", int(int(disk.Size) / 1024**3)))
            except Exception as e:
                attributes_tuples.append(("disk_error", str(e)))

    return attributes_tuples
                                           

def get_disk_type(file_path):
    current_platform = platform.system()

    if current_platform == "Linux":
        return get_linux_disk_type(file_path)
    elif current_platform == "Windows":
        return get_windows_disk_type(file_path)
    else:
        raise Exception("Unsupported platform")


def executable_path(file_path):
    """
    Get the absolute path to an executable file, suitable for both development and PyInstaller environments.
    
    In a PyInstaller environment, the application's directory path can be accessed via sys.executable. 
    In a development environment, the directory path of the __file__ is used as the base path.

    Args:
        file_path (str): The relative file path to the executable.

    Returns:
        str: The absolute path to the executable.
    """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return(os.path.join(application_path, file_path))
    
def create_random_file(file_name, size_mb):
    with open(file_name, 'wb') as f:
        f.write(os.urandom(size_mb * 1024 * 1024))

def ssh_speed_test(host, port, remote_path, local_path):
    # Setup the SSH client
    private_key_path = os.path.expanduser(executable_path("mykey"))
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
    client.connect(host, username='forensicinvestigator', key_filename=private_key_path, port=port)
    
    # Start the SFTP client
    sftp = client.open_sftp()

    # Measure upload speed
    start_time = time()
    sftp.put(local_path, remote_path)
    elapsed_time = time() - start_time
    file_size = os.path.getsize(local_path)
    upload_speed = file_size / elapsed_time  # in bytes per second

    # Clean up
    sftp.remove(remote_path)  # remove file from the server
    sftp.close()
    client.close()

    return upload_speed


class Benchmark:

    def __init__(self, file,write_mb, write_block_kb, read_block_b):
        self.file = file
        self.write_mb = write_mb
        self.write_block_kb = write_block_kb
        self.read_block_b = read_block_b
        self.wr_blocks = int(self.write_mb * 1024 / self.write_block_kb)
        self.rd_blocks = int(self.write_mb * 1024 * 1024 / self.read_block_b)
        
        
    
    def run_write_test(self):
        self.write_results = self.write_test( 1024 * self.write_block_kb, self.wr_blocks)
        
    def run_read_test(self):
        self.read_results = self.read_test(self.read_block_b, self.rd_blocks)

    def write_test(self, block_size, blocks_count, show_progress=True):
        '''
        Tests write speed by writing random blocks, at total quantity
        of blocks_count, each at size of block_size bytes to disk.
        Function returns a list of write times in sec of each block.
        '''
        f = os.open(self.file, os.O_CREAT | os.O_WRONLY, 0o777)  # low-level I/O

        took = []
        for i in range(blocks_count):
            if show_progress:
                # dirty trick to actually print progress on each iteration
                sys.stdout.write('\rWriting: {:.2f} %'.format(
                    (i + 1) * 100 / blocks_count))
                sys.stdout.flush()
            buff = os.urandom(block_size)
            start = time()
            os.write(f, buff)
            os.fsync(f)  # force write to disk
            t = time() - start
            took.append(t)

        os.close(f)
        return took

    def read_test(self, block_size, blocks_count, show_progress=True):
        '''
        Performs read speed test by reading random offset blocks from
        file, at maximum of blocks_count, each at size of block_size
        bytes until the End Of File reached.
        Returns a list of read times in sec of each block.
        '''
        f = os.open(self.file, os.O_RDONLY, 0o777)  # low-level I/O
        # generate random read positions
        offsets = list(range(0, blocks_count * block_size, block_size))
        shuffle(offsets)

        took = []
        for i, offset in enumerate(offsets, 1):
            if show_progress and i % int(self.write_block_kb * 1024 / self.read_block_b) == 0:
                # read is faster than write, so try to equalize print period
                sys.stdout.write('\rReading: {:.2f} %'.format(
                    (i + 1) * 100 / blocks_count))
                sys.stdout.flush()
            start = time()
            os.lseek(f, offset, os.SEEK_SET)  # set position
            buff = os.read(f, block_size)  # read from position
            t = time() - start
            if not buff: break  # if EOF reached
            took.append(t)

        os.close(f)
        return took
        
    def print_result(self):
        result = ('\n\nWritten {} MB in {:.4f} s\nWrite speed is  {:.2f} MB/s'
                  '\n  max: {max:.2f}, min: {min:.2f}\n'.format(
            self.write_mb, sum(self.write_results), self.write_mb / sum(self.write_results),
            max=self.write_block_kb / (1024 * min(self.write_results)),
            min=self.write_block_kb / (1024 * max(self.write_results))))
        result += ('\nRead {} x {} B blocks in {:.4f} s\nRead speed is  {:.2f} MB/s'
                   '\n  max: {max:.2f}, min: {min:.2f}\n'.format(
            len(self.read_results), self.read_block_b,
            sum(self.read_results), self.write_mb / sum(self.read_results),
            max=self.read_block_b / (1024 * 1024 * min(self.read_results)),
            min=self.read_block_b / (1024 * 1024 * max(self.read_results))))
        print(result)
    
    def get_write_result(self):
        write_info = ('written_MB', self.write_mb), ('total_write_time_s', sum(self.write_results)), ('write_speed_MBs', self.write_mb / sum(self.write_results)), ('max_speed_MBs', self.write_block_kb / (1024 * min(self.write_results))), ('min_speed_MBs', self.write_block_kb / (1024 * max(self.write_results)))           
        return write_info
    
    def get_read_result(self):
        
        read_info = ("read_speed_MBs", self.read_block_b / (1024 * 1024 * mean(self.read_results))), ("max_read_speed_MBs", self.read_block_b / (1024 * 1024 * min(self.read_results))), ("min_read_speed_MBs", self.read_block_b / (1024 * 1024 * max(self.read_results)))  

        print(read_info)
        return read_info
        

def getInternetSpeed():
    #global option    
    try:
        st = speedtest.Speedtest()       
        return ("internet_download", st.download()/1024**2), ("internet_upload", st.upload()/1024**2)
    except Exception as e:
        return ("Error_network_speed", str(e))

def getExternalIpv4():
    try:
        import re
        import json
        from urllib.request import urlopen

        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)
        #IP=data['ip']
        org=data['org']
        city = data['city']
        country=data['country']
        region=data['region']        
        return ("internet_provider", org), ("internet_country", country), ("internet_region", region), ("internet_city", city)
        #("external_ipv4", IP), 
        


    except Exception as e:
        return ("Error_ip", str(e))

def client_benchmark(forensic_image_path):   
    print("Getting disk type")
    forensic_stats = get_disk_type(forensic_image_path)

    print("Testing disk speed - get disk benchmark")    
    file = "benchmark.tmp"
    size = 128
    write_block_size = 1024
    read_block_size = 512    
    benchmark = Benchmark(file, size, write_block_size, read_block_size)
    benchmark.run_write_test()
    benchmark.run_read_test()    
    os.remove(file)
    
    
    forensic_stats.append(benchmark.get_read_result())
    forensic_stats.append(benchmark.get_write_result())
    
    
    # Get local cpu info
    print("Getting Cpu information")
    cpu_info_data = cpuinfo.get_cpu_info()    
    forensic_stats.append(("cpu_brand", cpu_info_data['brand_raw']))        
    forensic_stats.append(("cpu_speed", cpu_info_data['hz_advertised_friendly']))
    forensic_stats.append(("cpu_cores", cpu_info_data['count']))
    forensic_stats.append(("cpu_arch", cpu_info_data['bits']))

    print("SSH Upload speed test")
    # Test ssh upload speed
    host = '192.168.1.112'
    port = 22   
    local_path = 'local_random_file.txt'
    remote_path = '/tmp/random_file_to_test.txt'    
    # Create a random file of 100MB
    create_random_file(local_path, 100)
    # Perform the speed test
    upload_speed = ssh_speed_test(host, port, remote_path, local_path)
    # Remove the local file
    os.remove(local_path)        
    forensic_stats.append(("ssh_upload_speed_MBs", upload_speed/1024**2))    
    print("Internet speedtest")
    forensic_stats.append(getInternetSpeed())
    print("Internet Provider")
    forensic_stats.append(getExternalIpv4())
    
    print(forensic_stats)

def main():
    client_benchmark("D:\convertidos\MUS-CTF-19-DESKTOP-001\MUS-CTF-19-DESKTOP-001.E01")
   

if __name__ == "__main__":
    main()
