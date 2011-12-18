package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.EPQLibrary.FromSI;
import gov.nist.microanalysis.NISTMonte.Electron;

/**
 * Abstract detector for energy distribution.
 * 
 * @author ppinard
 */
public abstract class AbstractEnergyDetector extends AbstractChannelDetector {

    /**
     * Creates a new <code>AbstractEnergyDetector</code>.
     * 
     * @param min
     *            lower energy limit (in eV)
     * @param max
     *            upper energy limit (in eV)
     * @param channels
     *            number of channels (bins)
     */
    public AbstractEnergyDetector(double min, double max, int channels) {
        super(min, max, channels);
    }



    @Override
    public void backscatterEvent(Electron electron) {
        backscatterEvent(FromSI.eV(electron.getEnergy()));
    }



    @Override
    public void transmittedEvent(Electron electron) {
        transmittedEvent(FromSI.eV(electron.getEnergy()));
    }



    /**
     * Method called when an electron is backscattered.
     * 
     * @param energy
     *            electron energy in eV
     */
    public void backscatterEvent(double energy) {
        // Do nothing
    }



    /**
     * Method called when an electron is transmitted.
     * 
     * @param energy
     *            electron energy in eV
     */
    public void transmittedEvent(double energy) {
        // Do nothing
    }



    @Override
    public String getBinsHeader() {
        return "Energy (eV)";
    }

}
