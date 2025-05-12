import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import numpy as np

# Constants
WIDTH = 1000
HEIGHT = 1000
CENTER = np.array([0.0, 0.0, 0.0])  # Center of the simulation
PARTICLE_SIZE = 2.0  # Smaller for dust-like particles
NUM_PARTICLES = 500
VMAX = 200          # Max initial speed
FPS = 60
G = 5000            # Gravitational constant for central pull

# Initialize Pygame and OpenGL
pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
gluPerspective(45, (WIDTH / HEIGHT), 0.1, 2000.0)
glTranslatef(0.0, 0.0, -1000)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for glow
glEnable(GL_POINT_SMOOTH)           # Smooth points for glow effect

# Particle class
class CosmicParticle:
    def __init__(self):
        # Random initial position in a spherical volume
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(50, 400)  # Distance from center
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        self.pos = np.array([x, y, z])

        # Initial orbital velocity (tangential) + random component
        speed = random.uniform(50, VMAX)
        vel_dir = np.cross(self.pos, [0, 1, 0])  # Perpendicular to radius
        if np.linalg.norm(vel_dir) > 0:
            vel_dir = vel_dir / np.linalg.norm(vel_dir)
        self.vel = vel_dir * speed + np.random.uniform(-20, 20, 3)

        # Color with slight transparency for glow
        self.color = (
            random.uniform(0.5, 1.0),  # Red
            random.uniform(0.5, 1.0),  # Green
            random.uniform(0.5, 1.0),  # Blue
            random.uniform(0.2, 0.8)   # Alpha
        )

    def update(self, dt):
        # Gravitational force toward center
        r = np.linalg.norm(self.pos)
        if r > 0:
            gravity_dir = -self.pos / r
            gravity_magnitude = G / (r * r)  # Inverse square law
            gravity = gravity_dir * gravity_magnitude
            self.vel += gravity * dt

        # Update position
        self.pos += self.vel * dt

        # Dampen velocity to prevent extreme speeds near center
        if r < 50:  # Near center, slow down to avoid collapse
            self.vel *= 0.95

    def draw(self):
        glPointSize(PARTICLE_SIZE + 2 * math.sin(pygame.time.get_ticks() * 0.001))  # Pulsing effect
        glBegin(GL_POINTS)
        glColor4fv(self.color)
        glVertex3fv(self.pos)
        glEnd()

# Create particles
particles = [CosmicParticle() for _ in range(NUM_PARTICLES)]

# Draw a simple starry background
def draw_background():
    glBegin(GL_POINTS)
    for _ in range(200):  # 200 stars
        glColor3f(1.0, 1.0, 1.0)
        x = random.uniform(-1000, 1000)
        y = random.uniform(-1000, 1000)
        z = random.uniform(-1000, 1000)
        glVertex3f(x, y, z)
    glEnd()

# Main loop
running = True
angle = 0
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(FPS) / 1000.0

    # Update particles
    for particle in particles:
        particle.update(dt)

    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.1, 1.0)  # Dark blue background

    # Rotate view
    glPushMatrix()
    glRotatef(angle, 0, 1, 0)  # Rotate around y-axis
    angle += 0.5

    # Draw background and particles
    draw_background()
    for particle in particles:
        particle.draw()

    glPopMatrix()
    pygame.display.flip()

pygame.quit()