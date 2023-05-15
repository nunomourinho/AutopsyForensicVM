import PySimpleGUI as sg

# Define the layout
layout = [
    [sg.Image(filename='path_to_image.png')],
    [sg.Button('Button 1'), sg.Button('Button 2')]
]

# Create the window
window = sg.Window('Button with Picture Example', layout)

# Event loop
while True:
    event, values = window.read()

    # Exit if the window is closed
    if event == sg.WINDOW_CLOSED:
        break

    # Handle button events
    if event == 'Button 1':
        print('Button 1 clicked!')
    elif event == 'Button 2':
        print('Button 2 clicked!')

# Close the window
window.close()
