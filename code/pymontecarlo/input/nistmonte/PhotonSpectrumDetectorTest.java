package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.SpectrumProperties;
import gov.nist.microanalysis.EPQTools.EMSAFile;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Properties;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

import org.junit.Before;
import org.junit.Test;

import pymontecarlo.util.NistMonteTestCase;

public class PhotonSpectrumDetectorTest extends NistMonteTestCase {

    private PhotonSpectrumDetector det;

    private File resultFile;



    @Before
    public void setUp() throws Exception {
        double[] pos = getDetectorPosition();
        double emax = FromSI.eV(getBeamEnergy());
        det = new PhotonSpectrumDetector(pos, 0.0, emax, 100);
        resultFile = createTempFile("zip");

        MonteCarloSS mcss = getMonteCarloSS();
        XRayEventListener2 xrel = getXRayEventListener(mcss);
        BremsstrahlungEventListener bel = getBremsstrahlungEventListener(mcss);
        det.setup(mcss, xrel, bel);

        mcss.runTrajectory();
    }



    @Test
    public void testSaveResults() throws IOException, EPQException {
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        det.saveResults(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.emsa");
        assertNotNull(zipEntry);

        EMSAFile emsa = new EMSAFile();
        emsa.read(zipFile.getInputStream(zipEntry));
        assertEquals(128, emsa.getChannelCount()); // 100 force to 128
        assertEquals(150.0, emsa.getChannelWidth(), 1e-4);
        assertEquals(
                15.0,
                emsa.getProperties().getNumericProperty(
                        SpectrumProperties.BeamEnergy), 1e-4);

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
        assertEquals(8, props.size());

        zipFile.close();
    }

}
