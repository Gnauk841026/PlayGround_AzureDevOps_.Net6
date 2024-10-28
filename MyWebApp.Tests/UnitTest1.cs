using Microsoft.VisualStudio.TestTools.UnitTesting;
using MyWebApp; // 這裡需要引用原來的應用程式名稱

namespace MyWebAppTests
{
    [TestClass]
    public class MyServiceUnitTest
    {
        [TestMethod]
        public void TestGetGreetingMethod()
        {
            // Arrange
            MyService myService = new MyService();
            string expected = "Hello, welcome to Simple Web App!";

            // Act
            string result = myService.GetGreeting();

            // Assert
            Assert.AreEqual(expected, result);
        }
    }
}