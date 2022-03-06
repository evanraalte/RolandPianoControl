Revamped this repo into https://github.com/evanraalte/RolandPiano
Trying to keep it a bit simpler this time :)


# How this started

# Getting started

1. Install BluePy library: https://github.com/IanHarvey/bluepy
2. Add the following lines in `/etc/bluetooth/main.conf`:
    ``` 
     EnableLE = true           # Enable Low Energy support. Default is false.
     AttributeServer = true    # Enable the GATT attribute server. Default is false.
    ```
3. Make sure BlueZ (BluePy backend) can understand BLE midi:
    ```
    https://tttapa.github.io/Pages/Ubuntu/Software-Installation/BlueZ.html
    ```
4. Run application: `./app.py -m <mac_addr>  [--ambi_piano_gui]`
