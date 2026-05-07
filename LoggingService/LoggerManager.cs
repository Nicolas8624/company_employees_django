using Contracts;
using Serilog;
using System;
using System.Collections.Generic;
using System.Text;

namespace LoggingService
{
    public class LoggerManager : ILoggerManager
    {

        private readonly Serilog.ILogger _logger;

        public LoggerManager(Serilog.ILogger logger)
        {
            _logger = logger;
        }
        public void LogDebug(string message) => _logger.Debug(message);
        public void LogInformation(string message) => _logger.Information(message);
        public void LogWarning(string message) => _logger.Warning(message);
        public void LogError(string message) => _logger.Error(message);
    }
}
