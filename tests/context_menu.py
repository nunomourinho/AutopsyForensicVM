import winreg as reg
import os

def add_context_menu(filetype, name, command):
    """
    Adds a context menu entry to the specified filetype.
    
    filetype: the extension of the file, e.g., '.dd'
    name: the name of the context menu entry
    command: the command that the context menu will run
    """
    
    # Ensure filetype starts with a dot
    if not filetype.startswith("."):
        filetype = "." + filetype
    
    try:
        # Get the filetype (Progid)
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, filetype, 0, reg.KEY_READ) as key:
            progid = reg.QueryValue(key, "")
        
        # Define the path to the shell key
        shell_key_path = os.path.join(progid, "shell", name, "command")
        
        # Set the command
        with reg.CreateKey(reg.HKEY_CLASSES_ROOT, shell_key_path) as key:
            reg.SetValue(key, "", reg.REG_SZ, command)

        print(f"Context menu added for {filetype}")
    
    except Exception as e:
        print(f"Failed to add context menu for {filetype}. Error: {e}")

if __name__ == "__main__":
    # Filetype extensions
    filetypes = ['.dd', '.img', ,'.raw', '.aff', '.vmdk', '.e01']
    
    # Context menu name
    menu_name = "Convert forensic image to ForensicVM"
    
    # Command (replace with path to your program)
    cmd = r'"ForensicVMClient.bat" "%1"'
    
    for filetype in filetypes:
        add_context_menu(filetype, menu_name, cmd)
