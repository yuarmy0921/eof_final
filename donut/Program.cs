// See https://aka.ms/new-console-template for more information
// Solution
using System;
using System.Security.Cryptography;
using System.Text;

namespace Project_1
{
    class MainClass
    {
        public static void Main(string[] args)
        {
            for (int num = 1000; num < 10000; num++)
            {
                using MD5 mD = MD5.Create();
                byte[] bytes = Encoding.ASCII.GetBytes(num.ToString());
                byte[] array = mD.ComputeHash(bytes);
                BitConverter.ToString(array).Replace("-", string.Empty).ToLower();
                byte[] array2 = new byte[24]
                {
                    49, 8, 83, 209, 4, 77, 130, 36, 139, 44,
                    248, 52, 172, 0, 207, 23, 17, 27, 97, 254,
                    30, 116, 143, 28
                };

                for (int i = 0; i < array2.Length; i++)
                {
                    array2[i] ^= array[i % array.Length];
                }

                if (array2[0] == 70 || array2[0] == 102)
                {
                    Console.WriteLine(Encoding.UTF8.GetString(array2));
                }
            }
        }
    }
}
