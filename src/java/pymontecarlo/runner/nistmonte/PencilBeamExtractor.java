package pymontecarlo.runner.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.PencilBeam;

import java.io.IOException;

import org.jdom.Element;

/**
 * Extractor for a <code>PencilBeam</code>.
 * 
 * @author ppinard
 */
public class PencilBeamExtractor extends AbstractBeamExtractor {

    /** XML Tag. */
    private static final String TAG = "pymontecarlo.input.base.beam.PencilBeam";



    @Override
    public ElectronGun extract(Element beamImplElement) throws IOException,
            EPQException {
        PencilBeam beam = new PencilBeam();

        extractBeamEnergy(beamImplElement, beam);
        extractCenter(beamImplElement, beam);
        extractDirection(beamImplElement, beam);

        return beam;
    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }

}
