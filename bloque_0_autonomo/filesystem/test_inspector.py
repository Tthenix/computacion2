import unittest
from inspector import formatear_permisos, formatear_tamano

class TestInspector(unittest.TestCase):
    
    def test_formatear_permisos_basicos(self):
        # 0o644 -> 'rw-r--r--'
        self.assertEqual(formatear_permisos(0o644), "rw-r--r--")
        # 0o777 -> 'rwxrwxrwx' 
        self.assertEqual(formatear_permisos(0o777), "rwxrwxrwx")
        # 0o755 -> 'rwxr-xr-x'
        self.assertEqual(formatear_permisos(0o755), "rwxr-xr-x")
        # 0o000 -> '---------'
        self.assertEqual(formatear_permisos(0o000), "---------")

    def test_formatear_tamano_basicos(self):
        self.assertEqual(formatear_tamano(500), "500 B")
        self.assertEqual(formatear_tamano(1024), "1.00 KB")
        self.assertEqual(formatear_tamano(1048576), "1.00 MB")
        self.assertEqual(formatear_tamano(1073741824), "1.00 GB")

if __name__ == '__main__':
    unittest.main()
