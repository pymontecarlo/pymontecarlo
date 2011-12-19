package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;
import java.util.Properties;

import org.junit.Before;
import org.junit.Test;

import ptpshared.opencsv.CSVReader;
import pymontecarlo.util.NistMonteTestCase;

public class PhotonIntensityDetectorTest extends NistMonteTestCase {

    private PhotonIntensityDetector det;

    private File resultsDir;



    @Before
    public void setUp() throws Exception {
        det = new PhotonIntensityDetector(getDetectorPosition());
        resultsDir = createTempDir();

        MonteCarloSS mcss = getMonteCarloSS();
        XRayEventListener2 xrel = getXRayEventListener(mcss);
        det.setup(mcss, xrel, null);

        mcss.runTrajectory();
    }



    @Test
    public void testSaveResults() throws IOException {
        det.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(6, rows.get(0).length); // header
        assertEquals(62, rows.size() - 1); // x-ray transitions

        reader.close();
    }



    @Test
    public void testSaveLog() throws IOException {
        det.saveLog(resultsDir, "test");

        File logFile = new File(resultsDir, "test.log");
        assertTrue(logFile.exists());

        Properties props = new Properties();
        props.load(new FileInputStream(logFile));
        assertEquals(6, props.size());
    }
}
