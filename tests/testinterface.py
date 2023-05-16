import PySimpleGUI as sg
tabgroup =  sg.TabGroup([
                            [
                                sg.Tab('Sub Tab 1', [
                                    [sg.Text('Content inside Sub Tab 1')]
                                ]),
                                sg.Tab('Sub Tab 2', [
                                    [sg.Frame('Frame Inside Sub Tab 2', [
                                        [sg.Text('Content inside Frame')]
                                    ])]
                                ])
                            ]
                        ])
# Define the layout
layout = [
    [
        sg.TabGroup([
            [
                sg.Tab('Tab 1', [
                    [
                        sg.Column([[tabgroup],]),
                        sg.Column([
                            [sg.Text('Column 2, Row 1')],
                            [sg.Text('Column 2, Row 2')],
                        ])
                    ]
                ]),
                sg.Tab('Tab 2', [
                    [ sg.Text('Column 2, Row 2')
                    ]
                ])
            ]
        ])
    ]
]

# Create the window
window = sg.Window('Test Program', layout)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

# Close the window
window.close()
