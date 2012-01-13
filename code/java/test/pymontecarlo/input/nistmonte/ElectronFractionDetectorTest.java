package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Properties;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import org.jdom.Element;
import org.junit.Before;
import org.junit.Test;

import ptpshared.jdom.JDomUtils;
import pymontecarlo.util.NistMonteTestCase;

public class ElectronFractionDetectorTest extends NistMonteTestCase {

    private ElectronFractionDetector det;

    private File resultFile;



    @Before
    public void setUp() throws Exception {
        det = new ElectronFractionDetector();
        resultFile = createTempFile("zip");

        MonteCarloSS mcss = getMonteCarloSS();
        det.setup(mcss);

        mcss.runTrajectory();
    }



    @Test
    public void testSaveResults() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        det.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.xml");
        assertNotNull(zipEntry);

        Element element =
                JDomUtils.loadXML(zipFile.getInputStream(zipEntry))
                        .getRootElement();

        assertTrue(JDomUtils.hasChild(element, "backscattered"));
        assertTrue(JDomUtils.hasAttribute(element, "backscattered", "val"));

        assertTrue(JDomUtils.hasChild(element, "transmitted"));
        assertTrue(JDomUtils.hasAttribute(element, "transmitted", "val"));

        zipFile.close();
    }



    @Test
    public void testSaveLog() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        det.saveLog(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.log");
        assertNotNull(zipEntry);

        Properties props = new Properties();
        props.load(zipFile.getInputStream(zipEntry));
        assertEquals(4, props.size());

        zipFile.close();
    }

}
