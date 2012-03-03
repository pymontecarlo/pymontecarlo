package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.List;
import java.util.Properties;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import org.junit.Before;
import org.junit.Test;

import ptpshared.opencsv.CSVReader;
import pymontecarlo.util.NistMonteTestCase;

public class PhotonIntensityDetectorTest extends NistMonteTestCase {

    private PhotonIntensityDetector det;

    private File resultFile;



    @Before
    public void setUp() throws Exception {
        det = new PhotonIntensityDetector(getDetectorPosition());
        resultFile = createTempFile("zip");

        MonteCarloSS mcss = getMonteCarloSS();
        XRayEventListener2 xrel = getXRayEventListener(mcss);
        det.setup(mcss, xrel, null);

        mcss.runTrajectory();
    }



    @Test
    public void testSaveResults() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        det.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.csv");
        assertNotNull(zipEntry);

        Reader buf = new InputStreamReader(zipFile.getInputStream(zipEntry));
        CSVReader reader = new CSVReader(buf);
        List<String[]> rows = reader.readAll();

        assertEquals(18, rows.get(0).length); // header
        assertEquals(62, rows.size() - 1); // x-ray transitions

        reader.close();
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
        assertEquals(6, props.size());
    }
}
