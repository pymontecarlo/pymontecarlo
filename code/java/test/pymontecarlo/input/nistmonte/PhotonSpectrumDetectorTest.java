package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.SpectrumProperties;
import gov.nist.microanalysis.EPQTools.EMSAFile;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import org.junit.Before;
import org.junit.Test;

import pymontecarlo.util.NistMonteTestCase;

public class PhotonSpectrumDetectorTest extends NistMonteTestCase {

    private PhotonSpectrumDetector det;

    private File resultsDir;



    @Before
    public void setUp() throws Exception {
        double[] pos = getDetectorPosition();
        double emax = FromSI.eV(getBeamEnergy());
        det = new PhotonSpectrumDetector(pos, 0.0, emax, 100);
        resultsDir = createTempDir();

        MonteCarloSS mcss = getMonteCarloSS();
        XRayEventListener2 xrel = getXRayEventListener(mcss);
        BremsstrahlungEventListener bel = getBremsstrahlungEventListener(mcss);
        det.setup(mcss, xrel, bel);

        mcss.runTrajectory();
    }



    @Test
    public void testSaveResults() throws IOException, EPQException {
        det.saveResults(resultsDir, "test");

        File emsaFile = new File(resultsDir, "test.emsa");
        assertTrue(emsaFile.exists());

        EMSAFile emsa = new EMSAFile(emsaFile);
        assertEquals(128, emsa.getChannelCount()); // 100 force to 128
        assertEquals(150.0, emsa.getChannelWidth(), 1e-4);
        assertEquals(
                15.0,
                emsa.getProperties().getNumericProperty(
                        SpectrumProperties.BeamEnergy), 1e-4);
    }



    @Test
    public void testSaveLog() throws IOException {
        det.saveLog(resultsDir, "test");

        File logFile = new File(resultsDir, "test.log");
        assertTrue(logFile.exists());

        Properties props = new Properties();
        props.load(new FileInputStream(logFile));
        assertEquals(8, props.size());
    }

}
