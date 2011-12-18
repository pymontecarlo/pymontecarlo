package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.List;

import org.junit.Before;
import org.junit.Test;

import ptpshared.io.CSVReader;
import pymontecarlo.util.NistMonteTestCase;

public class EnergyDetectorFactoryTest extends NistMonteTestCase {

    private ElectronDetector detBSE;

    private ElectronDetector detTE;

    private File resultsDir;



    @Before
    public void setUp() throws Exception {
        resultsDir = new File("/tmp"); // createTempDir();

        double emax = getBeamEnergy();
        detBSE =
                EnergyDetectorFactory.createBackscatteredElectron(0, emax, 100);
        detTE = EnergyDetectorFactory.createTransmittedElectron(0, emax, 100);

        MonteCarloSS mcss = getMonteCarloSS();
        detBSE.setup(mcss);
        detTE.setup(mcss);

        mcss.runTrajectory();
    }



    @Test
    public void testCreateBackscatteredElectron() throws IOException {
        detBSE.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(100, rows.size() - 1); // bins

        reader.close();
    }



    @Test
    public void testCreateTransmittedElectron() throws IOException {
        detTE.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(100, rows.size() - 1); // bins

        reader.close();
    }

}
