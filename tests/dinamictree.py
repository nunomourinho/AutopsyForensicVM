import PySimpleGUI as psg

psg.set_options(font=("Arial Bold", 14))

treedata = psg.TreeData()

rootnodes = [
    ["", "MH", "Maharashtra", 175, 150, 200],
    ["MH", "MUM", "Mumbai", 100, 100, 100],
    ["MH", "PUN", "Pune", 30, 20, 40],
    ["MH", "NGP", "Nagpur", 45, 30, 60],
    ["", "TEL", "Telangana", 120, 80, 125],
    ["TEL", "HYD", "Hyderabad", 75, 55, 80],
    ["TEL", "SEC", "Secunderabad", 25, 15, 30],
    ["TEL", "NZB", "Nizamabad", 20, 10, 15]
]

for row in rootnodes:
    treedata.Insert(row[0], row[1], row[2], row[3:])

tree = psg.Tree(
    data=treedata,
    headings=['Product A', 'Product B', 'Product C'],
    auto_size_columns=True,
    select_mode=psg.TABLE_SELECT_MODE_EXTENDED,
    num_rows=10,
    col0_width=5,
    key='-TREE-',
    show_expanded=False,
    enable_events=True,
    expand_x=True,
    expand_y=True,
)

layout = [
          [psg.Button("Add Node", key='-ADD_NODE-')],
          [psg.Button("Delete All Nodes", key='-DELETE_ALL-')],
          [tree]
         ]
window = psg.Window("Tree Demo", layout, size=(715, 200), resizable=True)

while True:
    event, values = window.read()
    print("event:", event, "values:", values)
    if event == psg.WIN_CLOSED:
        break
    elif event == '-DELETE_ALL-':
        treedata = psg.TreeData()
        window['-TREE-'].update(treedata)
    elif event == '-ADD_NODE-':
        node_id = psg.popup_get_text("Enter Node ID:")
        if node_id:
            node_name = psg.popup_get_text("Enter Node Name:")
            if node_name:
                treedata.Insert("", node_id, node_name, [])
                window['-TREE-'].update(treedata)

window.close()
