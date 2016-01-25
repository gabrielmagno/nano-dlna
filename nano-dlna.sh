#!/bin/bash

gssdp-discover -n 5 | grep -A 1 "^  USN:.*urn:schemas-upnp-org:service:AVTransport" | sed -n 's/.*Location: \(.*\)/\1/p' > devices-ip.txt


