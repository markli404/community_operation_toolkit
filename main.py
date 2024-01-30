from plot.plot_util import *
from github.github_util import *
from dashboard.dashboard_util import *
if __name__ == '__main__':
    app = initiate_dashboard()
    app.run(debug=True)
