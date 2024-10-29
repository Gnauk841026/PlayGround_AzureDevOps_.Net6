using Microsoft.Extensions.DependencyInjection;
using Microsoft.VisualStudio.TestTools.UnitTesting;

[TestClass]
[TestCase(124)]
public class MyServiceUnitTest
{
    private ServiceProvider? _serviceProvider;

    [TestInitialize]
    public void Setup()
    {
        var serviceCollection = new ServiceCollection();
        serviceCollection.AddSingleton<MyService>();
        _serviceProvider = serviceCollection.BuildServiceProvider();
    }

    [TestCleanup]
    public void Cleanup()
    {
        if (_serviceProvider != null)
        {
            _serviceProvider.Dispose();
            _serviceProvider = null;
        }
    }

    [TestMethod]
    public void TestGetGreetingMethod()
    {
        // Arrange
        var myService = _serviceProvider?.GetService<MyService>();
        Assert.IsNotNull(myService, "MyService 應該被成功初始化");
        string expected = "Hello, welcome to Simple Web App!";

        // Act
        string result = myService!.GetGreeting();

        // Assert
        Assert.AreEqual(expected, result);
    }

    [TestMethod]
    public void TestAddMethod()
    {
        // Arrange
        var myService = _serviceProvider?.GetService<MyService>();
        Assert.IsNotNull(myService, "MyService 應該被成功初始化");
        int a = 5;
        int b = 3;
        int expected = 8;

        // Act
        int result = myService!.Add(a, b);

        // Assert
        Assert.AreEqual(expected, result);
    }

    [TestMethod]
    public void TestSubtractMethod()
    {
        // Arrange
        var myService = _serviceProvider?.GetService<MyService>();
        Assert.IsNotNull(myService, "MyService 應該被成功初始化");
        int a = 5;
        int b = 3;
        int expected = 2;

        // Act
        int result = myService!.Subtract(a, b);

        // Assert
        Assert.AreEqual(expected, result);
    }
}
