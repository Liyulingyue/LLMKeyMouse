from Tools.PicoContorller import PicoController

pico_controller = PicoController()

if __name__ == "__main__":
    pico_controller.set_socket(pico_address='192.168.2.244', pico_port=5000)
    pico_controller.send_to_pico("LED_ON[END]")
