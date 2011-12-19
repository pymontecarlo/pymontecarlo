package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;

import org.junit.Before;
import org.junit.Test;

import pymontecarlo.util.NistMonteTestCase;

public class ElectronFractionDetectorTest extends NistMonteTestCase {

    private ElectronFractionDetector det;

    private File resultsDir;



    @Before
    public void setUp() throws Exception {
        det = new ElectronFractionDetector();
        resultsDir = createTempDir();

        MonteCarloSS mcss = getMonteCarloSS();
        det.setup(mcss);

        mcss.runTrajectory();
    }



    @Test
    public void testSaveResults() throws IOException {
        det.saveResults(resultsDir, "test");

        File txtFile = new File(resultsDir, "test.txt");
        assertTrue(txtFile.exists());

        BufferedReader reader = new BufferedReader(new FileReader(txtFile));

        String line = reader.readLine();
        assertTrue(line.startsWith("Backscatter fraction:"));

        line = reader.readLine();
        assertTrue(line.startsWith("Transmitted fraction:"));

        assertNull(reader.readLine());

        reader.close();
    }



    @Test
    public void testSaveLog() throws IOException {
        det.saveLog(resultsDir, "test");

        File logFile = new File(resultsDir, "test.log");
        assertTrue(logFile.exists());

        Properties props = new Properties();
        props.load(new FileInputStream(logFile));
        assertEquals(4, props.size());
    }

}
