from email.utils import formataddr as format_email_addr
import email.header

def find_poc(pocs, role):
    recipients = []
    for poc in pocs:
        if poc.role == role and poc.email is not None:
            name = email.header.Header(poc.name)
            address = format_email_addr((name.encode(), poc.email))
            recipients.append(address)
    return recipients


def find_peering_poc(network):
    all_pocs = network.poc_set.all()

    recipients = []
    for role in ('Policy', 'Technical', 'NOC'):
        recipients = find_poc(all_pocs, role)
        if len(recipients) > 0:
            break

    return recipients
