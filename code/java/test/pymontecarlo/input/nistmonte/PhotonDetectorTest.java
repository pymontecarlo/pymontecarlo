package pymontecarlo.input.nistmonte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import gov.nist.microanalysis.EPQLibrary.EPQException;
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
        public void saveResults(ZipOutputStream zipOutput, String key)
                throws IOException {
        }



        @Override
        public boolean requiresBremsstrahlung() {
            return false;
        }



        @Override
        public String getPythonEquivalent() {
            return "pymontecarlo.result.base.result.PhotonDetectorMock";
        }

    }

    private PhotonDetector det;

    private File resultFile;



    @Before
    public void setUp() throws Exception {
        det = new PhotonDetectorMock(Math.toRadians(40.0), 0.0);
        resultFile = createTempFile("zip");
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
        ZipOutputStream zipOutput =
                new ZipOutputStream(new FileOutputStream(resultFile));
        det.saveLog(zipOutput, "test");
        zipOutput.close();

        ZipFile zipFile = new ZipFile(resultFile);
        ZipEntry zipEntry = zipFile.getEntry("test.log");
        assertNotNull(zipEntry);

        Properties props = new Properties();
        props.load(zipFile.getInputStream(zipEntry));
        assertEquals(5, props.size());

        zipFile.close();
    }

}
