from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=50)
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        submit_the_order(row)
    archive_receipts()
        
def open_robot_order_website():
    """"Navigates to the robot order website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Download the csv file read it as a table ad return it"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    orders_table = library.read_table_from_csv("orders.csv", header=True)
    return orders_table

def close_annoying_modal():
    """Clicks away the annoying modal popup"""
    page = browser.page()
    page.click("button:text('Ok')")

def fill_the_form(row):
    """fills the form with the order details and submits it"""
    page = browser.page()
    page.select_option("#head", str(row['Head']))
    page.click(f'#id-body-{row["Body"]}')
    page.fill("input[placeholder='Enter the part number for the legs']", str(row['Legs']))
    page.fill('#address', str(row['Address']))

def store_receipt_as_pdf(order_number):
    """Capture the order receipt and save it as a PDF file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_path = f"output/receipts/receipt_{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Takes a screenshot of the ordered robot and saves it as an image file"""
    page = browser.page()
    screenshot_path = f"output/screenshots/robot_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the robot screenshot to the PDF receipt"""
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[screenshot],
        target_document=pdf_file,
        append=True
    )
def submit_the_order(row):
    """Clicks the order button and retries stubbornly if the site errors out"""
    page = browser.page()
    order_num = row["Order number"]

    while True:
        page.click("button:text('Order')")

        receipt_visible = page.is_visible("#receipt")
        if receipt_visible:
            print(f"Order {order_num} submitted successfully! Generating artifacts...")
            pdf_path = store_receipt_as_pdf(order_num)
            screenshot_path = screenshot_robot(order_num)
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            break
        else:
            print(f"Server error detected for order {order_num}! Retrying submission...")

    page.click("button:text('ORDER ANOTHER ROBOT')")

def archive_receipts():
    """Creates a ZIP archive of the receipts and the screenshots"""
    archive = Archive()
    archive.archive_folder_with_zip(
        folder="output/receipts",
        archive_name="output/receipts.zip"
    )
    



    




