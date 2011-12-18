package pymontecarlo.input.nistmonte;

/**
 * Factory of angular detectors.
 * 
 * @author ppinard
 */
public class AngularDetectorFactory {

    /**
     * Angular elevation distribution of backscattered electrons.
     * 
     * @author ppinard
     */
    private static class BackscatteredElevationAngularDetector extends
            AbstractAngularDetector {

        /**
         * Creates a new <code>BackscatteredAngularDetector</code>.
         * 
         * @param min
         *            lower angular limit (in radians)
         * @param max
         *            upper angular limit (in radians)
         * @param channels
         *            number of channels (bins)
         */
        public BackscatteredElevationAngularDetector(double min, double max,
                int channels) {
            super(min, max, channels);
        }



        @Override
        public void backscatterEvent(double elevation, double azimuth) {
            histogram.add(elevation);
        }

    }

    /**
     * Angular azimuthal distribution of backscattered electrons.
     * 
     * @author ppinard
     */
    private static class BackscatteredAzimuthalAngularDetector extends
            AbstractAngularDetector {

        /**
         * Creates a new <code>BackscatteredAzimuthalAngularDetector</code>.
         * 
         * @param min
         *            lower angular limit (in radians)
         * @param max
         *            upper angular limit (in radians)
         * @param channels
         *            number of channels (bins)
         */
        public BackscatteredAzimuthalAngularDetector(double min, double max,
                int channels) {
            super(min, max, channels);
        }



        @Override
        public void backscatterEvent(double elevation, double azimuth) {
            histogram.add(azimuth);
        }

    }

    /**
     * Angular elevation distribution of transmitted electrons.
     * 
     * @author ppinard
     */
    private static class TransmittedElevationAngularDetector extends
            AbstractAngularDetector {

        /**
         * Creates a new <code>TransmittedElevationAngularDetector</code>.
         * 
         * @param min
         *            lower angular limit (in radians)
         * @param max
         *            upper angular limit (in radians)
         * @param channels
         *            number of channels (bins)
         */
        public TransmittedElevationAngularDetector(double min, double max,
                int channels) {
            super(min, max, channels);
        }



        @Override
        public void transmittedEvent(double elevation, double azimuth) {
            histogram.add(elevation);
        }

    }

    /**
     * Angular elevation distribution of transmitted electrons.
     * 
     * @author ppinard
     */
    private static class TransmittedAzimuthalAngularDetector extends
            AbstractAngularDetector {

        /**
         * Creates a new <code>TransmittedAzimuthalAngularDetector</code>.
         * 
         * @param min
         *            lower angular limit (in radians)
         * @param max
         *            upper angular limit (in radians)
         * @param channels
         *            number of channels (bins)
         */
        public TransmittedAzimuthalAngularDetector(double min, double max,
                int channels) {
            super(min, max, channels);
        }



        @Override
        public void transmittedEvent(double elevation, double azimuth) {
            histogram.add(azimuth);
        }

    }



    /**
     * Creates a new backscattered elevation angular detector.
     * 
     * @param min
     *            lower angular limit (in radians)
     * @param max
     *            upper angular limit (in radians)
     * @param channels
     *            number of channels (bins)
     * @return detector
     */
    public static final ElectronDetector createBackscatteredElevationAngular(
            double min, double max, int channels) {
        return new BackscatteredElevationAngularDetector(min, max, channels);
    }



    /**
     * Creates a new backscattered azimuthal angular detector.
     * 
     * @param min
     *            lower angular limit (in radians)
     * @param max
     *            upper angular limit (in radians)
     * @param channels
     *            number of channels (bins)
     * @return detector
     */
    public static final ElectronDetector createBackscatteredAzimuthalAngular(
            double min, double max, int channels) {
        return new BackscatteredAzimuthalAngularDetector(min, max, channels);
    }



    /**
     * Creates a new transmitted elevation angular detector.
     * 
     * @param min
     *            lower angular limit (in radians)
     * @param max
     *            upper angular limit (in radians)
     * @param channels
     *            number of channels (bins)
     * @return detector
     */
    public static final ElectronDetector createTransmittedElevationAngular(
            double min, double max, int channels) {
        return new TransmittedElevationAngularDetector(min, max, channels);
    }



    /**
     * Creates a new transmitted azimuthal angular detector.
     * 
     * @param min
     *            lower angular limit (in radians)
     * @param max
     *            upper angular limit (in radians)
     * @param channels
     *            number of channels (bins)
     * @return detector
     */
    public static final ElectronDetector createTransmittedAzimuthalAngular(
            double min, double max, int channels) {
        return new TransmittedAzimuthalAngularDetector(min, max, channels);
    }
}
