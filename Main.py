import PySimpleGUI as sg
import Reader as R
import pandas as pd

COLUMN_NAMES = ["Parcel ID","Owner","Lot Size","Land Assessed","Building Asessed","Total Assessed"
,"2021 tax","2020 tax","2019 tax","2018 tax","2017 tax"]
YEAR_LIST = [2021,2020]

data = pd.DataFrame(columns=COLUMN_NAMES)

sg.theme("BlueMono")
layout = [
    [sg.T("")], [sg.Text("Choose Files: "), sg.Input(key='_FILES_'), sg.FilesBrowse()],
    [sg.Text("Select Assessment Year"),sg.Combo(YEAR_LIST, default_value=YEAR_LIST[0], key="-YEAR-")],
    [sg.Button(button_text="Read Files",key="-READ-")],
    [sg.Table([], headings=COLUMN_NAMES, enable_events=True, expand_x=True, key='-TABLE-')],
    [sg.Button(button_text="Save Table",key="-SAVE-")]
]

###Building Window
window = sg.Window('Cook County Data Input', layout, size=(600,300))
    
while True:
    event, values = window.read()
    # print(values["-IN2-"])
    if event == sg.WIN_CLOSED:
        break
    elif event == "-READ-":
        files = values['_FILES_'].split(';')

        if files[0]=="":
            sg.popup("ERROR\nNo files selected.")
            continue

        #Checks for valid pdf format
        for f in files:
            if f[len(f)-3:len(f)] != "pdf":
                sg.popup("ERROR\nNot all files are pdfs")
                continue
        year = values["-YEAR-"]
        data = R.compile(files,COLUMN_NAMES,year)
        window.Element("-TABLE-").update(values=data.values.tolist())


    elif event == "-SAVE-":
        table = data.to_numpy()
        filename = sg.popup_get_file("Save As", default_extension='.csv', save_as=True, file_types=(("All CSV Files", "*.csv"),), no_window=True)
        if filename:
            try:
                with open(filename, 'wt') as f:
                    f.write('\n'.join([','.join(item) for item in [COLUMN_NAMES]+data.values.tolist()]))
                sg.popup(f"File {repr(filename)} Saved")
                continue
            except PermissionError:
                pass
        sg.popup(f"Cannot open file {repr(filename)}")


