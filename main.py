# start point
from mortgageMonitor import MortgageMonitor
from app import app


def main():
    # an instance of mortgage_monitor
    mortgage_monitor = MortgageMonitor()
    app.run(debug=True)


if __name__ == "__main__":
    main()
