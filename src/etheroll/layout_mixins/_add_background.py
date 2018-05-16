# flake8: noqa
###  PyPi  ###
from kivy.properties import ObjectProperty
from kivy.graphics   import Rectangle, Color


class Add_Background:
  background_color  = ObjectProperty(Color())
  _background_color = None
  _background       = None

  def on_parent(self, instance, value):
    _initialize_Background(self)
    _update_BackgroundSize(self, self.size)
    _update_BackgroundPosition(self, self.pos)
    self.bind(size=_update_BackgroundSize)
    self.bind(pos=_update_BackgroundPosition)
    self.bind(background_color=_update_BackgroundColor)


def _initialize_Background(instance):
  with instance.canvas.before:
    instance._background_color = Color(instance.background_color.rgba)
    instance._background       = Rectangle(pos=instance.pos, size=instance.size)

def _update_BackgroundColor(instance, rgba):
  instance._background_color.rgba = rgba
def _update_BackgroundSize(instance, size):
  instance._background.size = size
def _update_BackgroundPosition(instance, pos):
  instance._background.pos = pos

