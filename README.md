# python-proxy
A small proxy script to solve an issue with msgraph terraform provider

This script where created to solve an issue with the new [msgraph terraform provider](https://registry.terraform.io/providers/Microsoft/msgraph/latest/docs) that exist in version `0.1.1`.

### The Issue

The issue has been highlited in [some](https://github.com/microsoft/terraform-provider-msgraph/issues/26) [issues](https://github.com/microsoft/terraform-provider-msgraph/issues/27).

There is an race condition in which a resource that is created with the new provider are beeing checked to see if it exists right away. And for some resources like Conditional Access Policies do not have the time to be created before this check is made. And returns a `404 not found` error, and causes Terraform to throw an error.

This script solve this issue by replaying the latest request when an `404` error is recived a number of time (defaults to 3). When a successfull response is provided it will redirect it to Terraform. Or if the max retries is met, it will redirect the failed call to Terraform.

### Installation

The only python package requirements is `mitmproxy`.

It is recomended to install the dependency in a venv

Create the venv:
```
python -m venv venv
```

Activating the venv:
```
source venv/bin/activate
```

Then install mitmproxy
```
pip install mitmproxy
```

Or check the install inscrutions at mitmproxys [site](https://docs.mitmproxy.org/stable/overview/installation/)

Since the proxy inspects HTTPS traffic, a mitmproxy root cert is need to be installed in the az cli certificate trust.
To donwload the certificate follow the inscrution on mitmproxys site https://docs.mitmproxy.org/stable/concepts/certificates/

The certificate will need to be installed in the az clis certificate store, see these insstructions https://learn.microsoft.com/en-us/cli/azure/use-azure-cli-successfully-troubleshooting?view=azure-cli-latest#work-behind-a-proxy

### Usage

Start the script without optional arguemnts:
```
python3 proxy.py
```

Start the script with arguments:
```
python3 proxy.py --port 4444 --host 0.0.0.0 --retries 5
```

And then to run Terraform via proxyn:
````
HTTPS_PROXY=localhost:4444 terraform apply
````

or export the `HTTPS_PROXY` variable, but i would sugest to use the command above instead, since it might be required to switch between the proxy and not using the proxy see [Known issues](#Known-issues).

#### Arguments

`--port` which port the scripts listens to, if a port that is allready in use the script will fail (default: 8080)

`--host` which host the script listens to (default: 127.0.0.1)

`--retries` the max retries that will be allowed (default: 3)

### Known issues

The the first time trying to use the proxy and sometimes after that, az cli will still throw an `SSLError`, saying that to use a proxy the ceritficate will need to be added to az clis certificate store.

The workaround i have found is just to run Terraform without the proxy once (if using apply just abort the apply), and then run the Terraform command with the proxy again.