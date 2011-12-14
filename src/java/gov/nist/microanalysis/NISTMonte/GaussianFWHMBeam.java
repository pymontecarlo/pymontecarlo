package gov.nist.microanalysis.NISTMonte;

import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.Utility.Math2;

import java.util.Random;

/**
 * Electron beam where the diameter is specified at the FWHM.
 * 
 * @author ppinard
 */
public class GaussianFWHMBeam extends PencilBeam implements ElectronGun {

    /** Random number generator. */
    private final transient Random random = Math2.rgen;

    /** Beam diameter. */
    private double diameter;

    /** Conversion to Gaussian (1 sigma) to FWHM. */
    private static final double GAUSSIAN_TO_FWHM = Math.sqrt(2.0 * Math
            .log(2.0));



    /**
     * Creates a instance of the ElectronGun interface modeling a beam where the
     * diameter is specified at the FWHM.
     * 
     * @param diameter
     *            beam diameter at FWHM (in meters)
     */
    public GaussianFWHMBeam(double diameter) {
        setDiameter(diameter);
    }



    @Override
    public Electron createElectron() {
        final double[] initialPos = getCenter();
        final double r =
                random.nextGaussian() * GAUSSIAN_TO_FWHM * diameter / 2.0;
        final double th = 2.0 * Math.PI * random.nextDouble();
        initialPos[0] += r * Math.cos(th);
        initialPos[1] += r * Math.sin(th);
        return new Electron(initialPos, getTheta(), getPhi(), getBeamEnergy());
    }



    /**
     * Returns the beam diameter at FWHM (in meters).
     * 
     * @return beam diameter at FWHM (in meters).
     */
    public double getDiameter() {
        return diameter;
    }



    /**
     * Sets the beam diameter at FWHM.
     * 
     * @param diameter
     *            beam diameter at FWHM (in meters)
     * @throws IllegalArgumentException
     *             if the diameter is less than 0.0
     */
    public void setDiameter(double diameter) {
        if (diameter < 0.0)
            throw new IllegalArgumentException(
                    "Diameter must be greater or equal to 0.0");
        this.diameter = diameter;
    }

}
