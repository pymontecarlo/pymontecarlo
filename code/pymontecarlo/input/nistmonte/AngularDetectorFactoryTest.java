package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import org.junit.Before;
import org.junit.Test;

import ptpshared.opencsv.CSVReader;
import pymontecarlo.util.NistMonteTestCase;

public class AngularDetectorFactoryTest extends NistMonteTestCase {

    private ElectronDetector detBSEElevation;

    private ElectronDetector detBSEAzimuthal;

    private ElectronDetector detTEElevation;

    private ElectronDetector detTEAzimuthal;

    private File resultFile;



    @Before
    public void setUp() throws Exception {
        resultFile = createTempFile("zip");

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
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        detBSEElevation.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.csv");
        assertNotNull(zipEntry);

        Reader buf = new InputStreamReader(zipFile.getInputStream(zipEntry));
        CSVReader reader = new CSVReader(buf);
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(45, rows.size() - 1); // bins

        reader.close();
        zipFile.close();
    }



    @Test
    public void testCreateBackscatteredAzimuthalAngular() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        detBSEAzimuthal.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.csv");
        assertNotNull(zipEntry);

        Reader buf = new InputStreamReader(zipFile.getInputStream(zipEntry));
        CSVReader reader = new CSVReader(buf);
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(100, rows.size() - 1); // bins

        reader.close();
        zipFile.close();
    }



    @Test
    public void testCreateTransmittedElevationAngular() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        detTEElevation.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.csv");
        assertNotNull(zipEntry);

        Reader buf = new InputStreamReader(zipFile.getInputStream(zipEntry));
        CSVReader reader = new CSVReader(buf);
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(45, rows.size() - 1); // bins

        reader.close();
        zipFile.close();
    }



    @Test
    public void testCreateTransmittedAzimuthalAngular() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        detTEAzimuthal.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.csv");
        assertNotNull(zipEntry);

        Reader buf = new InputStreamReader(zipFile.getInputStream(zipEntry));
        CSVReader reader = new CSVReader(buf);
        List<String[]> rows = reader.readAll();

        assertEquals(2, rows.get(0).length); // header
        assertEquals(100, rows.size() - 1); // bins

        reader.close();
        zipFile.close();
    }

}
