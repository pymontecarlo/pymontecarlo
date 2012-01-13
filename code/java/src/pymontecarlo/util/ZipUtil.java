package pymontecarlo.util;

import java.io.IOException;
import java.io.StringWriter;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Utilities with ZIP inputs and outputs.
 * 
 * @author ppinard
 */
public class ZipUtil {

    /**
     * Saves a string buffer as a file inside the ZIP.
     * 
     * @param zipOutput
     *            ZIP output stream
     * @param name
     *            name of the file
     * @param buf
     *            string buffer
     * @throws IOException
     *             if an error occurs while saving
     */
    public static void saveStringBuffer(ZipOutputStream zipOutput, String name,
            StringBuffer buf) throws IOException {
        saveByteArray(zipOutput, name, buf.toString().getBytes());
    }



    /**
     * Saves a XML element as a file inside the ZIP.
     * 
     * @param zipOutput
     *            ZIP output stream
     * @param name
     *            name of the file
     * @param root
     *            XML element
     * @throws IOException
     *             if an error occurs while saving
     */
    public static void saveElement(ZipOutputStream zipOutput, String name,
            Element root) throws IOException {
        StringWriter sw = new StringWriter();
        JDomUtils.saveXML(root, sw);
        sw.close();

        saveStringBuffer(zipOutput, name, sw.getBuffer());
    }



    /**
     * Saves an array of bytes as a file inside a ZIP.
     * 
     * @param zipOutput
     *            ZIP output stream
     * @param name
     *            name of the file
     * @param bytes
     *            array of bytes
     * @throws IOException
     *             if an error occurs while saving
     */
    public static void saveByteArray(ZipOutputStream zipOutput, String name,
            byte[] bytes) throws IOException {
        ZipEntry zipEntry = new ZipEntry(name);
        zipOutput.putNextEntry(zipEntry);
        zipOutput.write(bytes, 0, bytes.length);
        zipOutput.closeEntry();
    }
}
