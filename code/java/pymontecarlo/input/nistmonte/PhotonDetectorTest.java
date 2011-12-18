package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import junittools.test.TestCase;

import org.junit.Before;
import org.junit.Test;

public class PhotonDetectorTest extends TestCase {

    private static class PhotonDetectorMock extends PhotonDetector {

        public PhotonDetectorMock(double takeOffAngle, double azimuthAngle) {
            super(takeOffAngle, azimuthAngle);
        }



        public PhotonDetectorMock(double[] pos) {
            super(pos);
        }



        @Override
        public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
                BremsstrahlungEventListener bel) throws EPQException {
        }



        @Override
        public void saveResults(File resultsDir, String baseName)
                throws IOException {
        }

    }

    private PhotonDetector det;

    private File resultsDir;



    @Before
    public void setUp() throws Exception {
        det = new PhotonDetectorMock(Math.toRadians(40.0), 0.0);
        resultsDir = createTempDir();
    }



    @Test
    public void testAbstractPhotonDetectorDoubleArray() {
        PhotonDetector det =
                new PhotonDetectorMock(new double[] { 0.01, 0.02, 0.03 });
        double[] pos = det.getDetectorPosition();
        assertEquals(0.01, pos[0], 1e-4);
        assertEquals(0.02, pos[1], 1e-4);
        assertEquals(0.03, pos[2], 1e-4);
    }



    @Test
    public void testGetDetectorPosition() {
        double[] pos = det.getDetectorPosition();
        assertEquals(0.07652784, pos[0], 1e-4);
        assertEquals(0.0, pos[1], 1e-4);
        assertEquals(0.06421448, pos[2], 1e-4);
    }



    @Test
    public void testGetTakeOffAngle() {
        assertEquals(Math.toRadians(40), det.getTakeOffAngle(), 1e-4);
    }



    @Test
    public void testGetAzimuthAngle() {
        assertEquals(Math.toRadians(0), det.getAzimuthAngle(), 1e-4);
    }



    @Test
    public void testSaveLog() throws IOException {
        det.saveLog(resultsDir, "test");

        File logFile = new File(resultsDir, "test.log");
        assertTrue(logFile.exists());

        Properties props = new Properties();
        props.load(new FileInputStream(logFile));
        assertEquals(5, props.size());
    }

}
