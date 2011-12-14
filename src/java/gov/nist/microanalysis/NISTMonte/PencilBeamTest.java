package gov.nist.microanalysis.NISTMonte;

import static org.junit.Assert.assertEquals;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.ToSI;

import org.junit.Before;
import org.junit.Test;

public class PencilBeamTest {

    private PencilBeam beam;



    @Before
    public void setUp() throws Exception {
        beam = new PencilBeam();
        beam.setCenter(new double[] { 1.0, 2.0, 3.0 });
        beam.setDirection(new double[] { 1.0, 2.0, 3.0 });
        beam.setBeamEnergy(ToSI.keV(5.0));
    }



    @Test
    public void testCreateElectron() {
        Electron e = beam.createElectron();
        assertEquals(5.0, FromSI.keV(e.getEnergy()), 1e-4);
    }



    @Test
    public void testPencilBeam() {
        assertEquals(1.0, beam.getCenter()[0], 1e-4);
        assertEquals(2.0, beam.getCenter()[1], 1e-4);
        assertEquals(3.0, beam.getCenter()[2], 1e-4);

        assertEquals(1.0, beam.getDirection()[0], 1e-4);
        assertEquals(2.0, beam.getDirection()[1], 1e-4);
        assertEquals(3.0, beam.getDirection()[2], 1e-4);

        assertEquals(5.0, FromSI.keV(beam.getBeamEnergy()), 1e-4);
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetBeamEnergyException() {
        beam.setBeamEnergy(0.0);
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetCenterException() {
        beam.setCenter(new double[] { 0.0, 0.0 });
    }



    @Test
    public void testSetDirection() {
        beam.setDirection(new double[] { 0.0, 0.0, 1.0 });
        assertEquals(0.0, beam.getTheta(), 1e-4);
        assertEquals(0.0, beam.getPhi(), 1e-4);

        beam.setDirection(new double[] { 0.0, 0.0, -1.0 });
        assertEquals(Math.PI, beam.getTheta(), 1e-4);
        assertEquals(0.0, beam.getPhi(), 1e-4);

        beam.setDirection(new double[] { 1.0, 1.0, 1.0 });
        assertEquals(Math.toRadians(54.7356), beam.getTheta(), 1e-4);
        assertEquals(Math.toRadians(45.0), beam.getPhi(), 1e-4);

        beam.setDirection(new double[] { 1.0, 1.0, -1.0 });
        assertEquals(Math.toRadians(180.0 - 54.7356), beam.getTheta(), 1e-4);
        assertEquals(Math.toRadians(45.0), beam.getPhi(), 1e-4);
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetDirectionException1() {
        beam.setDirection(new double[] { 0.0, 0.0 });
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetDirectionException2() {
        beam.setDirection(new double[] { 0.0, 0.0, 0.0 });
    }

}
