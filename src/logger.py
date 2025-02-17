from datetime import datetime
import os
import inspect
from enum import Enum


class LogMode(Enum):
    '''
    Enum class to define the log mode
    Either CONSOLE or FILE
    '''
    CONSOLE = 1
    FILE = 2


class LogLevel(Enum):
    '''
    Enum class to define the log level
    DEBUG, INFO, WARNING, ERROR, CRITICAL
    '''
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    FORENSIC = 60


class LineFileProvider:
    '''
    Class to provide the filename and line number of the caller
    '''

    @staticmethod
    def get_file_info():
        '''
        Get the filename and line number of the caller
        '''
        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        return filename, lineno


class JSJDLogger:
    '''
    Class to log messages to console or file
    '''

    _instance = None

    def __new__(cls, *args, **kwargs):
        '''
        Singleton pattern to ensure only one instance of the logger is created
        '''
        if cls._instance is None:
            cls._instance = super(JSJDLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename=None, level=LogLevel.DEBUG):
        '''
        Initialize the logger
        '''
        if hasattr(self, '_initialized'):
            return
        self._log_levels = {level.name: level.value for level in LogLevel}
        self._current_log_level = level.value
        self._console_mode = LogMode.CONSOLE
        self._file_mode = LogMode.FILE
        self._console_log_level = LogLevel.DEBUG
        self._file_log_level = LogLevel.ERROR
        self._file_handler = None
        self._log_directory = 'logs'
        self.setup_logging()
        self._initialized = True
        self.log_file_name = filename

    def setup_logging(self):
        if self._file_mode == LogMode.FILE and not self._file_handler:
            if not os.path.exists(self._log_directory):
                os.makedirs(self._log_directory)
        
        self.log_file_name = os.path.join(self._log_directory, datetime.now().strftime("%Y-%b-%d-%H-%M") + '.log')

        self._file_handler = open(self.log_file_name, 'a')

    def _print_to_console(self, level, message):
        color_codes = {
            LogLevel.DEBUG.value: "\033[94m",   # Blue
            LogLevel.INFO.value: "\033[92m",    # Green
            LogLevel.WARNING.value: "\033[93m",  # Yellow
            LogLevel.ERROR.value: "\033[91m",   # Red
            LogLevel.CRITICAL.value: "\033[95m",  # Magenta
            LogLevel.FORENSIC.value: "\033[96m"  # Cyan
        }
        color = color_codes.get(self._log_levels[level], "\033[0m")  # Default color (reset)
        reset_color = "\033[0m"
        print(f"{color}{message}{reset_color}")

    def log(self, level, message, args):
        filename, lineno = args

        assert filename is not None, "Filename cannot be None"
        assert lineno is not None, "Line number cannot be None"

        # Create the log message
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{current_time} - {level}: {filename}:{lineno} - {message}"

        # Print to console if console_mode is enabled
        if self._console_mode == LogMode.CONSOLE and self._log_levels[level] >= self._console_log_level.value:
            self._print_to_console(level, log_message)

        # Write to file if file_mode is enabled and a file_handler is set
        if self._file_mode and self._file_handler and self._log_levels[level] >= self._file_log_level.value:
            self._file_handler.write(log_message + '\n')
            self._file_handler.flush()

    def info(self, message, args):
        self.log("INFO", message, args)

    def debug(self, message, args):
        self.log("DEBUG", message, args)

    def warning(self, message, args):
        self.log("WARNING", message, args)

    def error(self, message, args):
        self.log("ERROR", message, args)

    def critical(self, message, args):
        self.log("CRITICAL", message, args)

    def forensic(self, message, args):
        self.log("FORENSIC", message, args)

    def set_console_mode(self, enabled):
        self.console_mode = enabled

    def set_file_mode(self, enabled):
        if enabled and not self._file_mode:
            self.setup_logging()
        elif not enabled and self._file_handler:
            self._file_handler.close()
            self._file_handler = None
        self._file_mode = enabled