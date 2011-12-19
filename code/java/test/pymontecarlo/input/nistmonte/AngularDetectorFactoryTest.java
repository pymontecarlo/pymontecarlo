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

import ptpshared.opencsv.CSVReader;
import pymontecarlo.util.NistMonteTestCase;

public class AngularDetectorFactoryTest extends NistMonteTestCase {

    private ElectronDetector detBSEElevation;

    private ElectronDetector detBSEAzimuthal;

    private ElectronDetector detTEElevation;

    private ElectronDetector detTEAzimuthal;

    private File resultsDir;



    @Before
    public void setUp() throws Exception {
        resultsDir = createTempDir();

        detBSEElevation =
                AngularDetectorFactory.createBackscatteredElevationAngular(0,
                        Math.toDegrees(90), 45);
        detBSEAzimuthal =
                AngularDetectorFactory.createBackscatteredAzimuthalAngular(0,
                        Math.toDegrees(360), 100);
        detTEElevation =
                AngularDetectorFactory.createBackscatteredElevationAngular(0,
                        Math.toDegrees(90), 45);
        detTEAzimuthal =
                AngularDetectorFactory.createBackscatteredAzimuthalAngular(0,
                        Math.toDegrees(360), 100);

        MonteCarloSS mcss = getMonteCarloSS();
        detBSEElevation.setup(mcss);
        detBSEAzimuthal.setup(mcss);
        detTEElevation.setup(mcss);
        detTEAzimuthal.setup(mcss);

        mcss.runTrajectory();
    }



    @Test
    public void testCreateBackscatteredElevationAngular() throws IOException {
        detBSEElevation.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(45, rows.size() - 1); // bins

        reader.close();
    }



    @Test
    public void testCreateBackscatteredAzimuthalAngular() throws IOException {
        detBSEAzimuthal.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(100, rows.size() - 1); // bins

        reader.close();
    }



    @Test
    public void testCreateTransmittedElevationAngular() throws IOException {
        detTEElevation.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(45, rows.size() - 1); // bins

        reader.close();
    }



    @Test
    public void testCreateTransmittedAzimuthalAngular() throws IOException {
        detTEAzimuthal.saveResults(resultsDir, "test");

        File csvFile = new File(resultsDir, "test.csv");
        assertTrue(csvFile.exists());

        CSVReader reader = new CSVReader(new FileReader(csvFile));
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(100, rows.size() - 1); // bins

        reader.close();
    }

}
