package pymontecarlo.program.nistmonte.input;

import gov.nist.microanalysis.NISTMonte.Electron;

/**
 * Abstract detector for angular distribution.
 * 
 * @author ppinard
 */
public abstract class AbstractAngularDetector extends AbstractChannelDetector {

    /**
     * Creates a new <code>AbstractAngularDetector</code>.
     * 
     * @param min
     *            lower angular limit (in radians)
     * @param max
     *            upper angular limit (in radians)
     * @param channels
     *            number of channels (bins)
     */
    public AbstractAngularDetector(double min, double max, int channels) {
        super(min, max, channels);
    }



    @Override
    public void backscatterEvent(Electron electron) {
        backscatterEvent(calculateElevationAngle(electron),
                calculateAzimuthalAngle(electron));
    }



    @Override
    public void transmittedEvent(Electron electron) {
        transmittedEvent(calculateElevationAngle(electron),
                calculateAzimuthalAngle(electron));
    }



    /**
     * Calculates the elevation angle (angle from the x-y plane).
     * 
     * @param electron
     *            backscattered or transmitted electron
     * @return elevation angle (in radians)
     */
    private double calculateElevationAngle(Electron electron) {
        double[] pos = electron.getPosition();
        return Math.atan2(pos[2], Math.sqrt(pos[0] * pos[0] + pos[1] * pos[1]));
    }



    /**
     * Calculates the azimuthal angle (CCW angle in the x-y plane from the +x
     * axis).
     * 
     * @param electron
     *            backscattered or transmitted electron
     * @return azimuthal angle (in radians)
     */
    private double calculateAzimuthalAngle(Electron electron) {
        double[] pos = electron.getPosition();

        double azimuth = Math.atan2(pos[1], pos[0]);
        if (azimuth < 0.0)
            azimuth = 2.0 * Math.PI + azimuth;

        return azimuth;
    }



    /**
     * Method called when an electron is backscattered.
     * 
     * @param elevation
     *            elevation angle of the electron (in radians)
     * @param azimuth
     *            azimuth angle of the electron (in radians)
     */
    public void backscatterEvent(double elevation, double azimuth) {

    }



    /**
     * Method called when an electron is transmitted.
     * 
     * @param elevation
     *            elevation angle of the electron (in radians)
     * @param azimuth
     *            azimuth angle of the electron (in radians)
     */
    public void transmittedEvent(double elevation, double azimuth) {

    }



    @Override
    public String getBinsHeader() {
        return "Angle (rad)";
    }

}
