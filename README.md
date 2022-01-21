# ids
identification service

error:
    UnicodeEncodeError: 'latin-1' codec can't encode characters... 

solution:
    # dpkg-reconfigure locales

    1. select ru.* kz.*
    2. next window select default: en_US.UTF8
    3. reboot system
