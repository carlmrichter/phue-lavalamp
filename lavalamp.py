from phue import Bridge
from threading import Timer
import random
import time
import datetime


class LavaLamp:

    switch_colors = False
    was_On = False

    def __init__(self, lights, alexa_light, transition_time, dev_output):
        if isinstance(dev_output, bool):
            self.dev_output = dev_output
        else:
            self.dev_output = False

        self.b = Bridge()
        print '[STATUS]{} Connected to Hue Bridge with IP {}'.format(self.get_time_string(), self.b.get_ip_address())

        self.light_names = self.b.get_light_objects('name')
        self.used_lights = lights
        self.alexa_light = alexa_light
        self.transition_time = transition_time
        self.last_hues = []
        self.initial_hues = []
        self.initial_saturation = []
        self.initial_brightness = []
        self.used_lights_without_alexa_light = []

        print '[STATUS]{} Used lights for LavaLamp:\n'.format(self.get_time_string())
        for light in self.used_lights:
            self.last_hues.append(self.light_names[light].hue)
            if not light == self.alexa_light:
                self.initial_hues.append(self.light_names[light].hue)
                self.initial_saturation.append(self.light_names[light].saturation)
                self.initial_brightness.append(self.light_names[light].brightness)
                self.used_lights_without_alexa_light.append(light)
            print light

    # generate time string for status messages
    def get_time_string(self):
        return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    # turn on all used lights
    def turn_On(self):
        for l in self.used_lights:
            self.light_names[l].on = True
        print '[STATUS]{} Turned on LavaLamp'.format(self.get_time_string())

    # set brightness of all used lights to specific value
    def set_brightness(self, brightness):
        if isinstance(brightness, int) and 0 <= brightness <= 254:
            for l in self.used_lights:
                self.light_names[l].brightness = brightness
        else:
            if self.dev_output:
                print '[DEV]{} Brightness have to be a value between 0 and 254'.format(self.get_time_string())

    # set saturation of all used lights to specific value
    def set_saturation(self, saturation):
        if isinstance(saturation, int) and 0 <= saturation <= 254:
            for l in self.used_lights:
                self.light_names[l].saturation = saturation
        else:
            if self.dev_output:
                print '[DEV]{} Saturation have to be a value between 0 and 254'.format(self.get_time_string())

    # generate new random colors for the used lights and change them to the new colors
    def new_random_colors(self):
        if len(self.used_lights) == 2:
            if self.switch_colors:
                self.last_hues[0], self.last_hues[1] = self.last_hues[1], self.last_hues[0]
                self.switch_colors = False
            else:
                for index, light in enumerate(self.used_lights):
                    self.last_hues[index] = random.randint(0, 65535)
                self.switch_colors = True

            for index, light in enumerate(self.used_lights):
                self.light_names[light].hue = self.last_hues[index]
                self.light_names[light].transitiontime = 10 * self.transition_time
                if self.dev_output:
                    print '[DEV]{} Light: {} -> New hue: {}'\
                        .format(self.get_time_string(), light, self.last_hues[index])
        else:
            print '[ERROR]{} Not implemented yet!'.format(self.get_time_string())

    # check if all of the lights are turned on
    def is_On(self):
        all_lights_on = True
        for light in self.used_lights:
            if not self.light_names[light].on:
                all_lights_on = False
                break
        return all_lights_on

    # match the brightness of all lights to the currently darkest one
    def match_brightness(self):
        brightness_values = []
        for l in self.used_lights:
            brightness_values.append(self.light_names[l].brightness)
        self.set_brightness(min(brightness_values))

    # reset transitiontime, hue, brightness and saturation of every light except for the alexa light
    def restore_original_state(self):
        for index, light in enumerate(self.used_lights_without_alexa_light):
            self.light_names[light].transitiontime = 4
            self.light_names[light].hue = self.initial_hues[index]
            self.light_names[light].saturation = self.initial_saturation[index]
            self.light_names[light].brightness = self.initial_brightness[index]

    # script loop - menu 1
    def loop_random(self):
        if raw_input('Start Color Loop now? (y/n) > ') in ['y', 'Y']:
            while True:
                if self.is_On():
                    if not self.was_On:
                        print '[STATUS]{} Starting color loop ...'.format(self.get_time_string())
                        for index, light in enumerate(self.used_lights_without_alexa_light):
                            self.initial_hues[index] = self.light_names[light].hue
                            self.initial_saturation[index] = self.light_names[light].saturation
                            self.initial_brightness[index] = self.light_names[light].brightness
                        self.set_saturation(254)
                        self.match_brightness()
                    self.was_On = True

                    t = Timer(self.transition_time, self.new_random_colors)
                    t.start()
                    t.join()
                else:
                    if self.was_On:
                        self.was_On = False
                        t = Timer(self.transition_time, self.restore_original_state)
                        t.start()
                        t.join()
                        print "[STATUS]{} Stopped color loop! Waiting for all lights to be turned on again ..." \
                            .format(self.get_time_string())
                    else:
                        time.sleep(1)

    def loop_same_colors(self):
        print "You've successfully entered loop_same_colors"

    def loop_custom_colors(self):
        print "You've successfully entered loop_custom_colors"

    def menu(self):
        options = {1: self.loop_random, 2: self.loop_same_colors, 3: self.loop_custom_colors}

        while True:
            print '\n----------------------------------------------'
            print '1 -- Random Loop'
            print '2 -- Random Loop with same Colors'
            print '3 -- Custom Color Loop'
            print '----------------------------------------------'
            num = int(raw_input('> '))
            if num in options:
                options[num]()
            else:
                print '[ERROR]{} Your choice is not a part of the menu!'.format(self.get_time_string())


lava = LavaLamp(['Oben', 'Unten'], 'Oben', 8, True)
lava.menu()









