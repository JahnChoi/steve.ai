import matplotlib.pyplot as plt

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')

class Graph:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        plt.title('Average Reward per Episode')
        plt.xlabel('Episode')
        plt.ylabel('Average Reward')
        plt.ion()
        plt.pause(0.001)

    def animate(self, xs, ys):
        self.ax.clear()
        self.ax.plot(xs, ys)
        plt.pause(0.001)
