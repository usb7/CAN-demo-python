Python3 demo code to receive and send CAN signals.

```bash
# Install and configure

# Log into CAN board and run below command
sudo apt install python3-pip
# Allow pip3 install packages in system dir
sudo mv /usr/lib/python$(python3 --version | grep -oPe '\d+.\d+')/EXTERNALLY-MANAGED /usr/lib/python$(python3 --version | grep -oPe '\d+.\d+')/EXTERNALLY-MANAGED.bak
sudo pip3 install cantools

# configure can0 interface
sudo ip link set can0 type can bitrate 500000
sudo ifconfig can0 up
```

```bash
# Usage

# Receive from CAN bus and decode
./receive.py --bus can0 --dbc ./Model3CAN.dbc

# Send CAN signals to CAN bus
./send.py --bus can0 --dbc ./Model3CAN.dbc --signal VCFRONT_turnSignalLeftStatus --value 1
```
