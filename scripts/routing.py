#Python script to simulate coin routing
from __future__ import print_function
import random

LOG_FILE_PATH = './log.txt'

def pay_invoice(sender, receiver, amt):
    log_file = open(LOG_FILE_PATH, "w+")

    print(str(sender) + ' paying ' + str(receiver) + ' ' + str(amt) + ' coins' + '...');
    log_file.write(str(sender) + ' paying ' + str(receiver) + ' ' + str(amt) + ' coins' + '...\n')

    # make invoice
    add_invoice = lncli_cmd.format(str(receiver), str(10000 + receiver), "addinvoice --amt=" + str(amt))
    invoice_string = cmd_async(add_invoice);
    log_file.write(add_invoice + '\n')

    invoice = json.loads(invoice_string);

    # pay invoice
    pay = lncli_cmd.format(str(sender), str(10000 + sender), "sendpayment -f --pay_req=" + invoice['pay_req'])
    receipt = cmd_async(pay)
    receipt = json.loads(receipt)
    log_file.write(pay + '\n')

    if receipt['payment_error'] == '':
        print("Success")
        print("---------------------------------------")

        log_file.write("SUCCESS")
        log_file.write(receipt)
        log_file.write("\n---------------------------------------\n")
    else:
        print("FAILED")
        print("---------------------------------------")

        log_file.write("FAILED")
        log_file.write(receipt)
        log_file.write("\n---------------------------------------\n")


def random(n):
    while True:
        s = -1
        r = -1
        a = 1

        # pick random sender
        s = int(random.random() * n)

        # pick random receiver
        r = int(random.random() * n)
        while r == s:
        # pick another val
        r = int(random.random() * n)

        pay_invoice(s, r, 5)

        time.sleep(.25)
    return

# network with one merchant
def merchant(n):
    while True:
        s = int(random.random() * (n - 1)) + 1
        r = 0   # first node is always merchant

        pay_invoice(s, r, 5)

        time.sleep(.25)

routing_types = {
    "random": random,
    "merchant": merchant
};
