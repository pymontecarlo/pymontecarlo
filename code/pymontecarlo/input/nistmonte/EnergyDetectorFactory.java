package pymontecarlo.input.nistmonte;

/**
 * Factory of energy detectors.
 * 
 * @author ppinard
 */
public class EnergyDetectorFactory {

    /**
     * Backscattered electron energy detector.
     * 
     * @author ppinard
     */
    private static class BackscatteredElectronEnergyDetector extends
            AbstractEnergyDetector {

        /**
         * Creates a new <code>BackscatteredElectronEnergyDetector</code>.
         * 
         * @param min
         *            lower energy limit (in eV)
         * @param max
         *            upper energy limit (in eV)
         * @param channels
         *            number of channels (bins)
         */
        public BackscatteredElectronEnergyDetector(double min, double max,
                int channels) {
            super(min, max, channels);
        }



        @Override
        public void backscatterEvent(double energy) {
            histogram.add(energy);
        }



        @Override
        public String getTag() {
            return "BackscatteredElectronEnergyResult";
        }

    }

    /**
     * Transmitted electron energy detector.
     * 
     * @author ppinard
     */
    private static class TransmittedElectronEnergyDetector extends
            AbstractEnergyDetector {

        /**
         * Creates a new <code>TransmittedElectronEnergyDetector</code>.
         * 
         * @param min
         *            lower energy limit (in eV)
         * @param max
         *            upper energy limit (in eV)
         * @param channels
         *            number of channels (bins)
         */
        public TransmittedElectronEnergyDetector(double min, double max,
                int channels) {
            super(min, max, channels);
        }



        @Override
        public void transmittedEvent(double energy) {
            histogram.add(energy);
        }



        @Override
        public String getTag() {
            return "TransmittedElectronEnergyResult";
        }
    }



    /**
     * Creates a backscattered electron energy detector.
     * 
     * @param min
     *            lower energy limit (in eV)
     * @param max
     *            upper energy limit (in eV)
     * @param channels
     *            number of channels (bins)
     * @return energy detector
     */
    public static ElectronDetector createBackscatteredElectron(double min,
            double max, int channels) {
        return new BackscatteredElectronEnergyDetector(min, max, channels);
    }



    /**
     * Creates a transmitted electron energy detector.
     * 
     * @param min
     *            lower energy limit (in eV)
     * @param max
     *            upper energy limit (in eV)
     * @param channels
     *            number of channels (bins)
     * @return energy detector
     */
    public static ElectronDetector createTransmittedElectron(double min,
            double max, int channels) {
        return new TransmittedElectronEnergyDetector(min, max, channels);
    }
}
