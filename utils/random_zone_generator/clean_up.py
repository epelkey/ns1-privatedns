"""
Script to clean up random zones generated by the gen_zones.py script. This
program finds any zones in a given account matching the regular expression
r"^zone\d+\.test\.?$" and sends a DELETE request to the API. Usage is similar
to gen_zones.py.
"""
import argparse
import requests
import re

if __name__ == "__main__":
    help_texts = {
        "main": __doc__,
        "api_host": "Address of the API container",
        "api_key": "API key to use",
        "org": (
            "Organization number to add the zones to \n"
            "(required with operator key)"
        ),
        "verify": "Disable SSL verification",
    }

    parser = argparse.ArgumentParser(
        description=help_texts["main"],
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-a",
        "--api_host",
        type=str,
        default="localhost",
        help=help_texts["api_host"],
    )

    parser.add_argument(
        "-o", "--org", type=int, default=0, help=help_texts["org"]
    )

    parser.add_argument(
        "-k", "--api_key", type=str, required=True, help=help_texts["api_key"]
    )

    parser.add_argument(
        "-v", "--verify", action="store_false", help=help_texts["verify"]
    )

    args = parser.parse_args()

    api_host = args.api_host
    api_key = args.api_key
    org = args.org
    verify = args.verify

    if not verify:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if org:
        header = {"X-NSONE-Key": f"{api_key}!{org}"}
    else:
        header = {"X-NSONE-Key": api_key}

    zones = requests.get(
        f"https://{api_host}/v1/zones", headers=header, verify=verify
    ).json()

    zone_name_pattern = re.compile(r"^zone\d+\.test\.?$")

    for zone in zones:
        if zone_name_pattern.match(zone["zone"]):
            resp = requests.delete(
                f"https://{api_host}/v1/zones/{zone['zone']}",
                headers=header,
                verify=verify,
            )

            print("*" * 120)
            print(
                f"Deleting zone '{zone['zone']}' - SSL verification: {verify} - Status:",
                resp.status_code,
            )
            if resp.status_code != 200:
                print(resp.text, resp.headers)
            else:
                print("Zone deleted")
            print("*" * 120)
