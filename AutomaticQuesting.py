import platform
import schedule
from time import sleep
from queue import Queue
from sys import version
from threading import Thread
from os import environ as env
from os import access, R_OK
import distro
from os.path import isdir, abspath, dirname, join
from argparse import ArgumentParser, RawTextHelpFormatter
from logging import getLogger, StreamHandler, Formatter, DEBUG
from automatic_questing.job import Job

from automatic_questing.aqlogger import AQLogger
from automatic_questing import VERSION, BRANCH, BUILD_DATE
from automatic_questing.iniparser import INIParser

PLATFORM_LINUX_DISTRO = f"{distro.id()} {distro.version()} {distro.name()}"


def thread(j, **kwargs):
    worker = Thread(target=j, kwargs=dict(**kwargs))
    worker.start()


if __name__ == "__main__":
    parser = ArgumentParser(prog='Automatic Questing',
                            description='Command-line utility to automatically send heroes from DFK on quests',
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-f", "--folder", help='Alternate data folder location')
    parser.add_argument("-v", "--verbose", action='store_true', help='Verbose logging')

    opts = parser.parse_args()

    tempLogger = getLogger('temp')
    tempLogger.setLevel(DEBUG)
    tempCh = StreamHandler()
    tempFormatter = Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S')
    tempCh.setFormatter(tempFormatter)
    tempLogger.addHandler(tempCh)

    DATA_FOLDER = env.get('AQ_FOLDER', vars(opts).get('folder') or abspath(join(dirname(__file__), 'data')))

    VERBOSE = env.get('AQ_VERBOSE', vars(opts).get('verbose'))

    if isdir(DATA_FOLDER):
        if not access(DATA_FOLDER, R_OK):
            tempLogger.error("Read permission error for %s", DATA_FOLDER)
            exit(1)
    else:
        tempLogger.error("%s does not exist", DATA_FOLDER)
        exit(1)

    # Initiate the logger
    aql = AQLogger(data_folder=DATA_FOLDER, debug=VERBOSE)
    aql.logger.info('Starting Automatic Questing...')

    aql.logger.info('Data folder is "%s"', DATA_FOLDER)

    aql.logger.info(u"%s %s (%s%s)", platform.system(), platform.release(), platform.version(),
                    ' - ' + PLATFORM_LINUX_DISTRO if PLATFORM_LINUX_DISTRO else '')

    aql.logger.info(u"Python %s", version)

    aql.logger.info("Automatic Questing v%s-%s %s", VERSION, BRANCH, BUILD_DATE)

    CONFIG = INIParser(DATA_FOLDER)
    QUEUE = Queue()

    for account in CONFIG.accounts:
        job = Job(CONFIG, account)
        at_time = schedule.every(CONFIG.interval).minutes
        at_time.do(thread, job.run).tag("account-{}".format(account))

    # Run all on startup
    schedule.run_all()

    while schedule.jobs:
        schedule.run_pending()
        sleep(1)
