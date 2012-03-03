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

public class EnergyDetectorFactoryTest extends NistMonteTestCase {

    private ElectronDetector detBSE;

    private ElectronDetector detTE;

    private File resultFile;



    @Before
    public void setUp() throws Exception {
        resultFile = createTempFile("zip");

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
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        detBSE.saveResults(zipOutput, "test");
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
    public void testCreateTransmittedElectron() throws IOException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        detTE.saveResults(zipOutput, "test");
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
