package gov.nist.microanalysis.NISTMonte;

import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.Utility.Math2;

/**
 * Electron gun with no diameter.
 * 
 * @author ppinard
 */
public class PencilBeam implements ElectronGun {

    /** Center position of the beam (in meters). */
    private double[] center;

    /** Direction of the electrons. */
    private double[] direction;

    /** Polar angle of the direction (in radians). */
    private double theta;

    /** Azimuthal angle of the direction (in radians). */
    private double phi;

    /** Beam energy. */
    private double energy;



    /**
     * Creates a new PencilBeam.
     * <p/>
     * By default, the electrons start at (0.0, 0.0, -0.99R) where R is the
     * chamber radius and move along the +z-axis.
     */
    public PencilBeam() {
        setCenter(Math2.multiply(0.99 * MonteCarloSS.ChamberRadius,
                Math2.MINUS_Z_AXIS));
        setDirection(new double[] { 0.0, 0.0, 1.0 });
    }



    @Override
    public Electron createElectron() {
        return new Electron(getCenter(), getTheta(), getPhi(), getBeamEnergy());
    }



    @Override
    public double getBeamEnergy() {
        return energy;
    }



    @Override
    public double[] getCenter() {
        return center.clone();
    }



    /**
     * Returns the direction vector of the electrons.
     * 
     * @return direction vector of the electrons
     */
    public double[] getDirection() {
        return direction;
    }



    /**
     * Returns the azimuthal angle of the direction (in radians).
     * 
     * @return azimuthal angle of the direction (in radians)
     */
    public double getPhi() {
        return phi;
    }



    /**
     * Returns the polar angle of the direction (in radians).
     * 
     * @return polar angle of the direction (in radians)
     */
    public double getTheta() {
        return theta;
    }



    @Override
    public void setBeamEnergy(double energy) {
        if (energy <= 0.0)
            throw new IllegalArgumentException("Energy must be greater than 0");
        this.energy = energy;
    }



    @Override
    public void setCenter(double[] center) {
        if (center.length != 3)
            throw new IllegalArgumentException(
                    "The position must be an array of length 3.");
        this.center = center.clone();
    }



    /**
     * Sets the direction vector of the electrons.
     * 
     * @param direction
     *            direction vector of the electrons
     * @throws IllegalArgumentException
     *             if the length of the vector is not 3
     * @throws IllegalArgumentException
     *             if the vector is the null vector
     */
    public void setDirection(double[] direction) {
        if (direction.length != 3)
            throw new IllegalArgumentException(
                    "The position must be an array of length 3.");
        if (Math2.magnitude(direction) == 0.0)
            throw new IllegalArgumentException(
                    "The norm of the vector must be different than zero");
        this.direction = direction;

        // From Weisstein, Eric W. "Spherical Coordinates."
        // From MathWorld--A Wolfram Web Resource.
        // http://mathworld.wolfram.com/SphericalCoordinates.html
        double r = Math2.magnitude(direction);
        theta = Math.acos(direction[2] / r);
        phi = Math.atan2(direction[1], direction[0]);
    }

}
