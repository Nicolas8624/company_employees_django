using System;
using System.Collections.Generic;
using System.Text;

namespace Contracts
{
    public interface ILoggerManager
    {
        void LogDebug(string message);
        void LogInformation(string message);
        void LogWarning(string message);
        void LogError(string message);

    }
}
