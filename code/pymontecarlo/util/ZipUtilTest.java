package pymontecarlo.util;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import org.jdom.Element;
import org.junit.Before;
import org.junit.Test;

import ptpshared.jdom.JDomUtils;

public class ZipUtilTest extends NistMonteTestCase {

    private File file;

    private ZipOutputStream zipOutput;



    @Before
    public void setUp() throws Exception {
        file = createTempFile("zip");
        zipOutput = new ZipOutputStream(new FileOutputStream(file));
    }



    @Test
    public void testSaveStringBuffer() throws IOException {
        // Save
        StringBuffer sb = new StringBuffer();
        sb.append("abc");

        ZipUtil.saveStringBuffer(zipOutput, "test", sb);
        zipOutput.close();

        // Test
        ZipFile zipFile = new ZipFile(file);
        ZipEntry zipEntry = zipFile.getEntry("test");
        assertNotNull(zipEntry);

        BufferedReader reader =
                new BufferedReader(new InputStreamReader(
                        zipFile.getInputStream(zipEntry)));
        String line = reader.readLine();
        assertEquals("abc", line);
    }



    @Test
    public void testSaveElement() throws IOException {
        // Save
        Element element = new Element("test");
        element.setAttribute("val", "abc");

        ZipUtil.saveElement(zipOutput, "test", element);
        zipOutput.close();

        // Test
        ZipFile zipFile = new ZipFile(file);
        ZipEntry zipEntry = zipFile.getEntry("test");
        assertNotNull(zipEntry);

        Element newElement =
                JDomUtils.loadXML(zipFile.getInputStream(zipEntry))
                        .getRootElement();
        assertEquals("abc", JDomUtils.getStringFromAttribute(newElement, "val"));
    }



    @Test
    public void testSaveByteArray() throws IOException {
        // Save
        byte[] array = { 'a', 'b', 'c' };

        ZipUtil.saveByteArray(zipOutput, "test", array);
        zipOutput.close();

        // Test
        ZipFile zipFile = new ZipFile(file);
        ZipEntry zipEntry = zipFile.getEntry("test");
        assertNotNull(zipEntry);

        BufferedReader reader =
                new BufferedReader(new InputStreamReader(
                        zipFile.getInputStream(zipEntry)));
        String line = reader.readLine();
        assertEquals("abc", line);
    }

}
