import win32com.client
import argparse
# import time


parser = argparse.ArgumentParser(
    description="Export SAP data"
)

parser.add_argument("--data", "-d", required=True, help="Master data to be downloaded - Vendor, Customer, Material")
args = parser.parse_args()

masterData = args.data

SapGuiAuto = win32com.client.GetObject("SAPGUI")
application = SapGuiAuto.GetScriptingEngine

print("✅ SAP GUI scripting engine found.")
print(f"Number of connections: {application.Children.Count}")

for i in range(application.Children.Count):
    conn = application.Children(i)
    print(f"Connection {i} has {conn.Children.Count} sessions.")

if application.Children.Count == 0:
    raise Exception("No SAP GUI session found. Please open and log into SAP first.")

connection = application.Children(0)

if connection.Children.Count == 0:
    raise Exception("SAP GUI session is open, but no active window found.")

session = connection.Children(0)

if masterData.lower() == 'vendor': tables = ['lfa1', 'lfb1', 'lfm1', 'lfbk']
elif masterData.lower() == 'customer': tables = ['kna1', 'knb1', 'knvv', 'knvk', 'knkk']
elif masterData.lower() == 'material': tables = ['mara', 'marc']

# Open SE16N
for table in tables:
    session.StartTransaction("SE16N")

    # Enter table name
    session.FindById("wnd[0]/usr/ctxtGD-TAB").Text = table
    session.findById("wnd[0]/usr/txtGD-MAX_LINES").text = ""
    session.FindById("wnd[0]/tbar[1]/btn[8]").Press()  # Execute

    # Execute to get data
    session.FindById("wnd[0]/tbar[1]/btn[8]").Press()
    
    # Export data
    session.FindById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").PressToolbarContextButton("&MB_EXPORT")
    session.FindById("wnd[0]/usr/cntlRESULT_LIST/shellcont/shell").SelectContextMenuItem("&XXL")
    session.FindById("wnd[1]/tbar[0]/btn[0]").Press()
    session.FindById("wnd[1]/usr/ctxtDY_FILENAME").Text = f"{table}_export.xlsx"
    session.FindById("wnd[1]/tbar[0]/btn[0]").Press()
    # print("✅ Export complete")
