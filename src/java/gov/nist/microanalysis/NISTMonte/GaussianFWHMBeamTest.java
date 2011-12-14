package gov.nist.microanalysis.NISTMonte;

import static org.junit.Assert.assertEquals;
import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.EPQLibrary.ToSI;

import org.junit.Before;
import org.junit.Test;

public class GaussianFWHMBeamTest {

    private GaussianFWHMBeam beam;



    @Before
    public void setUp() throws Exception {
        beam = new GaussianFWHMBeam(10e-9);
        beam.setCenter(new double[] { 1.0, 2.0, 3.0 });
        beam.setBeamEnergy(ToSI.keV(5.0));
    }



    @Test
    public void testCreateElectron() {
        Electron e = beam.createElectron();
        assertEquals(5.0, FromSI.keV(e.getEnergy()), 1e-4);
    }



    @Test
    public void testFWHMBeam() {
        assertEquals(10.0, beam.getDiameter() * 1e9, 1e-4);
        assertEquals(1.0, beam.getCenter()[0], 1e-4);
        assertEquals(2.0, beam.getCenter()[1], 1e-4);
        assertEquals(3.0, beam.getCenter()[2], 1e-4);
        assertEquals(5.0, FromSI.keV(beam.getBeamEnergy()), 1e-4);
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetBeamEnergy() {
        beam.setBeamEnergy(0.0);
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetCenter() {
        beam.setCenter(new double[] { 0.0, 0.0 });
    }



    @Test(expected = IllegalArgumentException.class)
    public void testSetDiameter() {
        beam.setDiameter(-1.0);
    }

}
