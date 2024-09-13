import ctypes
from datetime import datetime
from picosdk.usbtc08 import usbtc08 as tc08
from picosdk.functions import assert_pico2000_ok

def collect_temperature_data(start_time, num_samples=15):
    """
    Collects temperature data from the PicoLog TC-08 device.

    Parameters:
        start_time (datetime): The start time of the data collection.
        num_samples (int): The number of samples to collect.

    Returns:
        list: A list of dictionaries containing timestamps and temperature readings.
    """
    # Ensure start_time is a datetime object
    if not isinstance(start_time, datetime):
        raise ValueError("start_time must be a datetime object")
    
    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}

    # Open unit
    status["open_unit"] = tc08.usb_tc08_open_unit()
    assert_pico2000_ok(status["open_unit"])
    chandle = status["open_unit"]

    # Set mains rejection to 50 Hz
    status["set_mains"] = tc08.usb_tc08_set_mains(chandle, 0)
    assert_pico2000_ok(status["set_mains"])

    # Set up channel for type S thermocouple
    typeS = ctypes.c_int8(83)
    status["set_channel"] = tc08.usb_tc08_set_channel(chandle, 1, typeS)
    assert_pico2000_ok(status["set_channel"])

    # Get minimum sampling interval in ms
    status["get_minimum_interval_ms"] = tc08.usb_tc08_get_minimum_interval_ms(chandle)
    assert_pico2000_ok(status["get_minimum_interval_ms"])

    # List to store the collected data
    temperature_data = []
    
    # Collect the samples
    for i in range(num_samples):
        # Get single temperature reading
        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)
        units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
        status["get_single"] = tc08.usb_tc08_get_single(chandle, ctypes.byref(temp), ctypes.byref(overflow), units)
        assert_pico2000_ok(status["get_single"])

        # Capture the current time
        current_time = datetime.now()

        # Calculate elapsed time since start
        elapsed_time = current_time - start_time

        # Format elapsed time as HH:MM:SS.SS
        total_seconds = elapsed_time.total_seconds()
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        formatted_elapsed_time = f"{int(hours):02}:{int(minutes):02}:{seconds:05.2f}"

        # Save the data
        temperature_data.append({
            "time": formatted_elapsed_time,
            "cold_junction_temp": temp[0],
            "channel_1_temp": temp[1]
        })

        # Print data with timestamp
        print(f"{formatted_elapsed_time} seconds, {temp[0]:.2f} °C, {temp[1]:.2f} °C")

    # Close unit
    status["close_unit"] = tc08.usb_tc08_close_unit(chandle)
    assert_pico2000_ok(status["close_unit"])

    # Return the collected data
    return temperature_data
